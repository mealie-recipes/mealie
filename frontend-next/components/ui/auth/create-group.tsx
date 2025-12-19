"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "../checkbox";
import { Check } from "lucide-react";
import { useRegistration } from "./registration-context";

/**
 * Render the "Create Group" registration step and handle updating registration state and navigation.
 *
 * Renders input and validation states for a required group name, options for private recipes and seed data, and Back/Continue controls. When the entered group name is valid, continuing updates the registration data with the group name and advances to the next step.
 *
 * @returns The React element tree for the create-group step of the registration flow.
 */
export function CreateGroup() {
  const { goNext, goBack, updateData, data, validations } = useRegistration();
  const { groupName } = validations;

  const handleContinue = async () => {
    if (!groupName.value.trim()) {
      return;
    }

    if (groupName.error) {
      return;
    }

    if (!groupName.isValid) {
      return;
    }

    updateData({ groupName: groupName.value });
    goNext();
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300 mx-auto max-w-[270px] sm:max-w-[325px]">
      <p className="text-sm text-muted-foreground">
        Before you create an account you'll need to create a group. Your group
        will only contain you, but you'll be able to invite others later.
        Members in your group can share meal plans, shopping lists, recipes, and
        more!
      </p>
      <div className="space-y-2">
        <Label htmlFor="group-name">Group Name*</Label>
        <Input
          id="group-name"
          placeholder="Enter group name"
          value={groupName.value}
          onChange={(e) => groupName.setValue(e.target.value)}
          required
          aria-invalid={!!groupName.error}
        />
        {groupName.isChecking && (
          <p className="text-xs text-muted-foreground text-right">
            Checking availability...
          </p>
        )}
        {groupName.isValid && !groupName.isChecking && (
          <p className="text-xs text-green-500 flex items-center gap-1 justify-end">
            <Check className="h-3 w-3" />
            Group name is available!
          </p>
        )}
        {groupName.error && (
          <p className="text-xs text-destructive text-right">
            {groupName.error}
          </p>
        )}
        <div className="flex items-center mt-6">
          <Checkbox
            id="private-recipes"
            checked={data.privateRecipes || false}
            onCheckedChange={(checked) =>
              updateData({ privateRecipes: checked === true })
            }
          />
          <Label htmlFor="private-recipes" className="ml-2">
            Keep My Recipes Private
          </Label>
        </div>
        <p className="text-xs text-muted-foreground">
          Sets your group and all recipes defaults to private. You can always
          change this later.
        </p>
        <div className="flex items-center mt-6">
          <Checkbox
            id="seed-data"
            checked={data.seedData || false}
            onCheckedChange={(checked) =>
              updateData({ seedData: checked === true })
            }
          />
          <Label htmlFor="seed-data" className="ml-2">
            Seed Data
          </Label>
        </div>
        <p className="text-xs text-muted-foreground">
          Mealie ships with a collection of Foods, Units, and Labels that can be
          used to populate your group with helpful data for organizing your
          recipes. These are translated into the language you currently have
          selected. You can always add to or modify this data later.
        </p>
      </div>
      <div className="flex justify-end gap-4">
        <Button variant="outline" onClick={goBack} className="">
          Back
        </Button>
        <Button
          disabled={
            groupName.isChecking ||
            !groupName.value.trim() ||
            !!groupName.error ||
            !groupName.isValid
          }
          onClick={handleContinue}
        >
          Continue
        </Button>
      </div>
    </div>
  );
}
