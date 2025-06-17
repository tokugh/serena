import { BaseClass, Processable } from './BaseClass';

export class ConcreteProcessor extends BaseClass implements Processable {
    private data: string[];

    constructor(name: string) {
        super(name);
        this.data = [];
    }

    execute(): void {
        console.log(`Executing processor ${this.name}`);
        this.process();
    }

    process(): void {
        console.log(`Processing data: ${this.data.join(', ')}`);
    }

    getType(): string {
        return 'ConcreteProcessor';
    }

    addData(item: string): void {
        this.data.push(item);
    }
}