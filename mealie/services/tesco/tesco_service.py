import json
import re
import logging
from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession, Session
from mealie.schema.tesco import TescoProduct

logger = logging.getLogger(__name__)

class TescoService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        }

    async def get_product_price(self, product_url: str) -> TescoProduct:
        product_data = TescoProduct(url=product_url)
        
        logger.debug(f"Fetching Tesco URL: {product_url}...")
        
        async with AsyncSession(impersonate="chrome") as session:
            try:
                response = await session.get(product_url, headers=self.headers)
                product_data.status_code = response.status_code
                
                if response.status_code == 200:
                    logger.debug(f"Successfully fetched HTML for: {product_url}")
                    self._parse_html(response.text, product_data, product_url)
                else:
                    logger.warning(f"Failed to fetch {product_url}: {response.status_code}")

            except Exception as e:
                logger.error(f"Error fetching {product_url}: {e}")

        return product_data

    def get_product_price_sync(self, product_url: str) -> TescoProduct:
        product_data = TescoProduct(url=product_url)
        
        logger.debug(f"Fetching Tesco URL (Sync): {product_url}...")
        
        with Session(impersonate="chrome") as session:
            try:
                response = session.get(product_url, headers=self.headers)
                product_data.status_code = response.status_code
                
                if response.status_code == 200:
                    logger.debug(f"Successfully fetched HTML for: {product_url}")
                    self._parse_html(response.text, product_data, product_url)
                else:
                    logger.warning(f"Failed to fetch {product_url}: {response.status_code}")

            except Exception as e:
                logger.error(f"Error fetching {product_url}: {e}")

        return product_data

    def _parse_html(self, html_content: str, product_data: TescoProduct, product_url: str):
        soup = BeautifulSoup(html_content, 'html.parser')
        product_data.scrape_success = True

        # Method 1: JSON-LD
        script_tag = soup.find('script', type='application/ld+json', attrs={'data-mfe-head': 'data-mfe-head'})
        if script_tag:
            try:
                json_data = json.loads(script_tag.string)
                if isinstance(json_data, dict) and "@graph" in json_data:
                    for item in json_data["@graph"]:
                        if item.get("@type") == "Product":
                            product_data.name = item.get("name")
                            offers = item.get("offers")
                            if offers and isinstance(offers, dict):
                                product_data.price = float(offers.get("price")) if offers.get("price") else None
                                product_data.price_valid_until = offers.get("priceValidUntil")
            except json.JSONDecodeError as e:
                logger.warning(f"Could not decode JSON-LD for {product_url}: {e}")
            except Exception as e:
                logger.error(f"Error parsing JSON-LD for {product_url}: {e}")

        # Method 2: Discover JSON (for quantity/units)
        script_tag_2 = soup.find('script', type='application/discover+json')
        if script_tag_2 and script_tag_2.contents:
            try:
                loaded_json = json.loads(script_tag_2.contents[0])
                product_id = product_url.split('/')[-1]
                
                # Helper for nested JSON
                def open_nested_json(data, path_list):
                    for key in path_list:
                        if isinstance(data, dict) and key in data:
                            data = data[key]
                        else:
                            return None
                    return data

                core_list = ['mfe-orchestrator', 'props', 'apolloCache', f'ProductType:{product_id}']
                details_json = open_nested_json(loaded_json, core_list)
                
                if details_json:
                    # Pack Size
                    pack_size_list = ['details', 'packSize']
                    pack_size = open_nested_json(details_json, pack_size_list)
                    
                    if pack_size:
                        value = pack_size[0].get('value')
                        units = pack_size[0].get('units', '').lower()
                        
                        if value is not None:
                            value = float(value)
                            if units == 'g':
                                value = value / 1000
                                units = 'kg'
                            
                            product_data.quantity = value
                            product_data.units = units

                    # Price Per Unit
                    price_list = ['price']
                    price_json = open_nested_json(details_json, price_list)
                    
                    if price_json:
                        price = price_json.get('actual')
                        unit_price = price_json.get('unitPrice')
                        unit_of_measure = price_json.get('unitOfMeasure', '').lower()
                        
                        if unit_price is not None:
                            unit_price = float(unit_price)
                            if unit_of_measure == '100g':
                                unit_price = unit_price * 10
                                unit_of_measure = 'kg'
                            
                            product_data.price_per_unit = unit_price
                            
                            if unit_of_measure == 'each':
                                product_data.units = 'each'
                                if price and unit_price:
                                    product_data.quantity = round(price / unit_price)

            except Exception as e:
                logger.error(f"Error parsing discover+json for {product_url}: {e}")

        # Fallback/Confirmation for Price Per Unit from HTML text
        if product_data.price_valid_until:
            price_per_unit_element = soup.find('p', class_='ddsweb-text styled__SubText-sc-1d7lp92-11 gsjoLn ddsweb-value-bar__content-subtext a9556a_GlysEa_text a9556a_GlysEa_shortFormXs')
        else:
            price_per_unit_element = soup.find('p', class_='ddsweb-text styled__Subtext-sc-v0qv7n-2 nsITR ddsweb-price__subtext a9556a_GlysEa_text a9556a_GlysEa_shortFormSm')

        if price_per_unit_element and not product_data.price_per_unit:
            text = price_per_unit_element.text.strip()
            # Data returned is e.g. (£1.23/kg)
            price_per_unit_match = re.findall(r'[0-9]+\.[0-9]+', text)
            if len(price_per_unit_match) == 1:
                try:
                    units_match = re.findall(r'[a-zA-Z]+', text.split('/')[1])
                    if units_match:
                        units = units_match[0]
                        product_data.price_per_unit = float(price_per_unit_match[0])
                        product_data.units = units
                        
                        if product_data.price and product_data.price_per_unit:
                             qty = round(product_data.price / product_data.price_per_unit, 3)
                             if units == 'each':
                                 product_data.quantity = int(qty)
                             else:
                                 product_data.quantity = qty
                except Exception as e:
                    logger.error(f"Error parsing price per unit text: {e}")

    def sync_all_prices(self, session):
        from sqlalchemy import select
        from mealie.db.models.recipe.recipe_ingredient import RecipeIngredient
        
        logger.info("Starting Tesco Price Sync...")
        
        stmt = select(RecipeIngredient).where(RecipeIngredient.tesco_product_url.is_not(None))
        result = session.execute(stmt)
        ingredients = result.scalars().all()
        
        logger.info(f"Found {len(ingredients)} ingredients with Tesco URLs.")
        
        # Use sync session
        with Session(impersonate="chrome") as client:
            for ingredient in ingredients:
                try:
                    url = ingredient.tesco_product_url
                    if not url:
                        continue
                        
                    logger.debug(f"Syncing: {ingredient.note} ({url})")
                    
                    # Use sync method
                    product_data = self.get_product_price_sync(url)
                    
                    if product_data.scrape_success and product_data.price is not None:
                        logger.info(f"Updating price: {ingredient.tesco_price} -> {product_data.price}")
                        ingredient.tesco_price = product_data.price
                        
                except Exception as e:
                    logger.error(f"Error syncing ingredient {ingredient.id}: {e}")
        
        session.commit()
        logger.info("Tesco Price Sync Completed.")
