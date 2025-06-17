<?php

abstract class BaseClass 
{
    protected string $name;

    public function __construct(string $name) 
    {
        $this->name = $name;
    }

    abstract public function execute(): void;

    public function getName(): string 
    {
        return $this->name;
    }
}

interface Processable 
{
    public function process(): void;
    public function getType(): string;
}

interface Readable 
{
    public function read(): string;
}

interface Writable 
{
    public function write(string $data): void;
}