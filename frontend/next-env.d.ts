/// <reference types="next" />
/// <reference types="next/image-types/global" />
/// <reference types="next/navigation" />

declare module "*.css" {
  const content: { [className: string]: string };
  export default content;
}