import {
  mdiBookOpenPageVariant,
  mdiChefHat,
  mdiGrill,
  mdiMicrowave,
  mdiPot,
  mdiPotSteamOutline,
  mdiRice,
  mdiSmoke,
  mdiStove,
  mdiThermometerWater,
  mdiToasterOven,
  mdiWeatherWindy,
} from "@mdi/js";

export interface CookingMethodOption {
  name: string;
  icon: string;
}

export const cookingMethodOptions: CookingMethodOption[] = [
  { name: "Oven", icon: mdiToasterOven },
  { name: "Air Fryer", icon: mdiWeatherWindy },
  { name: "Slow Cooker", icon: mdiPotSteamOutline },
  { name: "Pressure Cooker", icon: mdiPot },
  { name: "Stovetop", icon: mdiStove },
  { name: "Grill / BBQ", icon: mdiGrill },
  { name: "Microwave", icon: mdiMicrowave },
  { name: "Smoker", icon: mdiSmoke },
  { name: "Sous Vide", icon: mdiThermometerWater },
  { name: "Rice Cooker", icon: mdiRice },
];

export const originalCookingMethodIcon = mdiBookOpenPageVariant;

export function getCookingMethodIcon(method: string | null | undefined): string {
  if (!method) return originalCookingMethodIcon;

  const normalized = method.trim().toLocaleLowerCase();
  return cookingMethodOptions.find(option => option.name.toLocaleLowerCase() === normalized)?.icon || mdiChefHat;
}
