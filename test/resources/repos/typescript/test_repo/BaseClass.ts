export abstract class BaseClass {
    protected name: string;

    constructor(name: string) {
        this.name = name;
    }

    abstract execute(): void;

    getName(): string {
        return this.name;
    }
}

export interface Processable {
    process(): void;
    getType(): string;
}

export interface Readable {
    read(): string;
}

export interface Writable {
    write(data: string): void;
}