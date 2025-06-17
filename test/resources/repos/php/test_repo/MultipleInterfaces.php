<?php

require_once 'BaseClass.php';

class MultipleInterfaces implements Readable, Writable, Processable 
{
    private string $data;

    public function __construct(string $data) 
    {
        $this->data = $data;
    }

    public function read(): string 
    {
        return $this->data;
    }

    public function write(string $data): void 
    {
        $this->data = $data;
    }

    public function process(): void 
    {
        echo "Processing data: {$this->data}\n";
    }

    public function getType(): string 
    {
        return "MultipleInterfaces";
    }
}