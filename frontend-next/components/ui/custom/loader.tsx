import { Loader2 } from "lucide-react";

/**
 * Renders a centered spinning loader with the label "Loading..." and entrance animations.
 *
 * @returns A JSX element containing a centered spinning Loader2 icon and the text "Loading..." styled with entrance animation classes.
 */
export default function Loader() {
  return (
    <div className="text-center flex flex-col items-center justify-center animate-in fade-in slide-in-from-right-2 duration-500">
      <Loader2 className="h-8 w-8 animate-spin text-orange-400" />
      <p className="mt-4 ml-2 text-zinc-600 dark:text-zinc-400">Loading...</p>
    </div>
  );
}