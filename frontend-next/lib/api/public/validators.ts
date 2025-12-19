const prefix = "/api";

const routes = {
  group: (name: string) =>
    `${prefix}/validators/group?name=${encodeURIComponent(name)}`,
  household: (name: string) =>
    `${prefix}/validators/household?name=${encodeURIComponent(name)}`,
  user: (name: string) =>
    `${prefix}/validators/user/name?name=${encodeURIComponent(name)}`,
  email: (name: string) =>
    `${prefix}/validators/user/email?email=${encodeURIComponent(name)}`,
  recipe: (groupId: string, name: string) =>
    `${prefix}/validators/recipe?group_id=${encodeURIComponent(
      groupId
    )}&name=${encodeURIComponent(name)}`,
};

/**
 * Fetches the availability of the given type and value.
 * @param type - The type of value to validate (e.g., 'group', 'household', 'user', 'email', 'recipe').
 * @param value - The value to validate.
 * @returns A promise that resolves to a boolean indicating whether the value is available.
 */
export async function validateAvailability(
  type: "group" | "household" | "user" | "email" | "recipe",
  value: string,
  groupId?: string
): Promise<boolean> {
  const response = await fetch(getValidationUrl(type, value, groupId), {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store", // Always fetch fresh validation
  });

  if (!response.ok) {
    throw new Error(`Failed to validate ${type}: ${response.statusText}`);
  }

  const data = await response.json();
  return data.valid;
}

/**
 * Constructs the validation URL based on the type and value.
 * @param type - The type of value to validate.
 * @param value - The value to validate.
 * @param groupId - The group ID (required for 'recipe' type).
 * @returns The constructed validation URL.
 */
function getValidationUrl(
  type: "group" | "household" | "user" | "email" | "recipe",
  value: string,
  groupId?: string
): string {
  switch (type) {
    case "group":
      return routes.group(value);
    case "household":
      return routes.household(value);
    case "user":
      return routes.user(value);
    case "email":
      return routes.email(value);
    case "recipe":
      if (!groupId) {
        throw new Error("groupId is required for recipe validation");
      }
      return routes.recipe(groupId, value);
    default:
      throw new Error(`Unknown validation type: ${type}`);
  }
}
