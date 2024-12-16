import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function capitalize(str: string) {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

export function capitalizeWords(str: string) {
  return str
    .split(' ')
    .map((word) => capitalize(word))
    .join(' ');
}

export function waitForElement<TElement extends Element = Element>(
  selector: string,
  callback: (element: NodeListOf<TElement>) => void,
) {
  let tries = 0;

  const intervalId = setInterval(() => {
    const element = document.querySelectorAll(selector) as NodeListOf<TElement>;

    if (element.length > 0) {
      clearInterval(intervalId);
      callback(element);
    } else {
      tries++;
      if (tries > 50) {
        clearInterval(intervalId);
        console.log(
          `waitForElement :: element "${selector}" not found [this is not an error]`,
        );
      }
    }
  }, 500);
}
