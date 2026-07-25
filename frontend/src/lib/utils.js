// cn(): merge Tailwind class names (clsx + tailwind-merge). Used by all shadcn components.
import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}
