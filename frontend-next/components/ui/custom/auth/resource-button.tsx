import { Button } from "@/components/ui/button";
import { type LucideIcon } from "lucide-react";
import { type ReactNode } from "react";

interface ResourceButtonProps {
  href: string;
  icon: LucideIcon;
  children: ReactNode;
}

export const ResourceButton = ({
  href,
  icon: Icon,
  children,
}: ResourceButtonProps) => {
  return (
    <Button
      nativeButton={false}
      variant="outline"
      size="sm"
      className="bg-secondary hover:bg-secondary/80 text-black dark:text-white"
      render={(props) => (
        <a {...props} href={href} target="_blank" rel="noopener noreferrer">
          <Icon className="mr-2 h-4 w-4" />
          {children}
        </a>
      )}
    />
  );
};
