// Type declarations for jsonpath module
declare module 'jsonpath' {
  export function query(obj: any, pathExpression: string): any[];
  export function paths(obj: any, pathExpression: string): any[];
  export function nodes(obj: any, pathExpression: string): any[];
  export function value(obj: any, pathExpression: string): any;
  export function parent(obj: any, pathExpression: string): any;
  export function apply(obj: any, pathExpression: string, fn: (value: any) => any): any;
  export function parse(pathExpression: string): any;
  export function stringify(path: any): string;
}
