import { ComponentExample } from "@/components/component-example";
import { LogoutButton } from "@/components/ui/logout-button";

export default function Page() {
  return (
    <div className="p-4 space-y-4">
      <LogoutButton />
      <ComponentExample />
    </div>
  );
}
