import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const alertVariants = cva(
  "grid gap-0.5 rounded-lg border px-2 py-1.5 text-left text-xs/relaxed has-data-[slot=alert-action]:relative has-data-[slot=alert-action]:pr-18 has-[>svg]:grid-cols-[auto_1fr] has-[>svg]:gap-x-1.5 *:[svg]:row-span-2 *:[svg]:translate-y-0.5 *:[svg]:text-current *:[svg:not([class*='size-'])]:size-3.5 w-full relative group/alert",
  {
    // variants: {
    //   variant: {
    //     default: "bg-card text-card-foreground",
    //     destructive:
    //       "text-destructive bg-card *:data-[slot=alert-description]:text-destructive/90 *:[svg]:text-current",
    //     info: "bg-card text-blue-900 *:data-[slot=alert-description]:text-blue-900/90 *:[svg]:text-blue-500",
    //     success:
    //       "bg-card text-green-900 *:data-[slot=alert-description]:text-green-900/90 *:[svg]:text-green-500",
    //     warning:
    //       "bg-card text-yellow-900 *:data-[slot=alert-description]:text-yellow-900/90 *:[svg]:text-yellow-500",
    //   },
    // },
    variants: {
      variant: {
        default: "bg-card text-card-foreground border-border",
        destructive:
          "bg-red-50 text-red-900 dark:bg-red-900/20 dark:text-red-200 dark:border-red-900 border-red-200 *:data-[slot=alert-description]:text-red-900/90 dark:*:data-[slot=alert-description]:text-red-200/90 *:[svg]:text-red-500 dark:*:[svg]:text-red-400",
        info: "bg-blue-50 text-blue-900 dark:bg-blue-950 dark:text-blue-50 dark:border-blue-800 border-blue-200 *:data-[slot=alert-description]:text-blue-900/90 dark:*:data-[slot=alert-description]:text-blue-100 *:[svg]:text-blue-600 dark:*:[svg]:text-blue-400",
        success:
          "bg-green-50 text-green-900 dark:bg-green-900/20 dark:text-green-200 dark:border-green-900 border-green-200 *:data-[slot=alert-description]:text-green-900/90 dark:*:data-[slot=alert-description]:text-green-200/90 *:[svg]:text-green-600 dark:*:[svg]:text-green-400",
        warning:
          "bg-yellow-50 text-yellow-900 dark:bg-yellow-900/20 dark:text-yellow-200 dark:border-yellow-900 border-yellow-200 *:data-[slot=alert-description]:text-yellow-900/90 dark:*:data-[slot=alert-description]:text-yellow-200/90 *:[svg]:text-yellow-600 dark:*:[svg]:text-yellow-400",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

function Alert({
  className,
  variant,
  ...props
}: React.ComponentProps<"div"> & VariantProps<typeof alertVariants>) {
  return (
    <div
      data-slot="alert"
      role="alert"
      className={cn(alertVariants({ variant }), className)}
      {...props}
    />
  );
}

function AlertTitle({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="alert-title"
      className={cn(
        "font-medium group-has-[>svg]/alert:col-start-2 [&_a]:hover:text-foreground [&_a]:underline [&_a]:underline-offset-3",
        className
      )}
      {...props}
    />
  );
}

function AlertDescription({
  className,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="alert-description"
      className={cn(
        "text-muted-foreground text-xs/relaxed md:text-pretty [&_p:not(:last-child)]:mb-4 [&_a]:hover:text-foreground [&_a]:underline [&_a]:underline-offset-3",
        className
      )}
      {...props}
    />
  );
}

function AlertAction({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="alert-action"
      className={cn("absolute top-1.5 right-2", className)}
      {...props}
    />
  );
}

export { Alert, AlertTitle, AlertDescription, AlertAction };
