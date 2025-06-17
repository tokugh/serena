import { Readable, Writable, Processable } from './BaseClass';

export class MultipleInterfaces implements Readable, Writable, Processable {
    private data: string;

    constructor(data: string) {
        this.data = data;
    }

    read(): string {
        return this.data;
    }

    write(data: string): void {
        this.data = data;
    }

    process(): void {
        console.log(`Processing data: ${this.data}`);
    }

    getType(): string {
        return 'MultipleInterfaces';
    }
}