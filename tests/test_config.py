from pathlib import Path

CWD = Path(__file__).parent


TEST_DIR = CWD
TEST_DATA = CWD.joinpath("data")

# Scraper
TEST_RAW_HTML = TEST_DATA.joinpath("scraper", "html-raw")
TEST_RAW_RECIPES = TEST_DATA.joinpath("scraper", "recipes-raw")

# Migrations
TEST_CHOWDOWN_DIR = TEST_DATA.joinpath("migrations", "chowdown")
TEST_NEXTCLOUD_DIR = TEST_DATA.joinpath("migrations", "nextcloud")
TEST_CSV_DIR = TEST_DATA.joinpath("migrations", "csv")

# Routes

if __name__ == "__main__":
    pass
