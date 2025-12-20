import { ComponentExample } from "@/components/component-example";
import { LogoutButton } from "@/components/ui/logout-button";

/**
 * Renders a padded vertical container that displays a logout button above a component example.
 *
 * @returns A React element containing a div with padding and vertical spacing that renders `LogoutButton` followed by `ComponentExample`.
 */
export default function Page() {
  return (
    <div className="p-4 space-y-4">
      <LogoutButton />
      <ComponentExample />
    </div>
  );
}