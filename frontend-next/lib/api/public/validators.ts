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
 * Check whether a given identifier or resource name is available on the server.
 *
 * @param type - The kind of value to validate: "group", "household", "user", "email", or "recipe".
 * @param value - The identifier or name to check for availability.
 * @param groupId - Required when `type` is "recipe"; the group ID that the recipe belongs to.
 * @returns `true` if the value is available, `false` otherwise.
 * @throws Error when the validation endpoint responds with a non-OK status or when a required `groupId` is missing for `recipe` validations.
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
 * Build the API URL used to validate a given resource value.
 *
 * @param type - The kind of resource to validate: "group", "household", "user", "email", or "recipe"
 * @param value - The resource value to validate (will be encoded by the route builder)
 * @param groupId - The group ID required when `type` is "recipe"
 * @returns The full validation URL for the specified resource and value
 * @throws Error if `type` is "recipe" and `groupId` is not provided
 * @throws Error if `type` is not one of the supported validation types
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
