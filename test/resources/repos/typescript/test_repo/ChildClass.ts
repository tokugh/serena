import { BaseClass } from './BaseClass';

export class ChildClass extends BaseClass {
    private value: number;

    constructor(name: string, value: number) {
        super(name);
        this.value = value;
    }

    execute(): void {
        console.log(`Executing ${this.name} with value ${this.value}`);
    }

    getValue(): number {
        return this.value;
    }
}