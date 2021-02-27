declare module 'babyparse' {
  declare function unparse(options: {fields: string[], data: (?Object)[]}): string;
  declare function parse(text: string, options: {header: boolean, delimiter: string, comments: boolean, skipEmptyLines: boolean}): {data: any};
};

declare module 'lodash' {
  declare function cloneDeep<T>(obj: T): T;
  declare function isEmpty(obj: Object): boolean;
  declare function range(start: number, end: number): [];
};

declare class jquerySelector {
  hide(): void;
  show(): void;
  pickadate(): void;
  on(string, function): void;
  click(): void;
};

declare module 'jquery' {
  declare var exports: (selector: string) => jquerySelector;
};

declare module 'materialize' {
  declare var exports: any;
};

declare module 'keymirror' {
  declare var exports: ({ [string]: null }) => { [string]: string };
};

declare module 'autobind-decorator' {
  declare var exports: any;
};

declare module 'react-immutable-proptypes' {
  declare var exports: any;
};

declare module 'materialize-css' {
  declare var exports: any;
};

declare module 'react-sortable-hoc' {
  declare var exports: any;
};

declare module 'react-materialize' {
  declare var exports: any;
};

declare module 'canvas-gauges' {
  declare var exports: any;
};

declare module 'sweetalert' {
  declare var exports: any;
};

declare module 'ajv' {
  declare var exports: any;
};

declare module 'jquery.scrollto' {
  declare var exports: any;
};

declare module 'md5' {
  declare var exports: (str: string) => string;
};
