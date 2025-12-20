import { Heart, GithubIcon, Folder, GitBranch } from "lucide-react";
import { ResourceButton } from "@/components/ui/custom/auth/resource-button";

export const ProjectLinks = () => {
  return (
    <div className="flex gap-4 justify-center items-center">
      <ResourceButton href="https://github.com/sponsors/hay-kot" icon={Heart}>
        Sponsor
      </ResourceButton>

      {/* <ResourceButton
        href="https://github.com/mealie-recipes/mealie"
        icon={GithubIcon}
      >
        Mealie Original
      </ResourceButton> */}

      <ResourceButton
        href="https://github.com/blawson490/mealie-next/"
        icon={GitBranch}
      >
        Mealie Next
      </ResourceButton>

      <ResourceButton href="https://docs.mealie.io/" icon={Folder}>
        Docs
      </ResourceButton>
    </div>
  );
};
