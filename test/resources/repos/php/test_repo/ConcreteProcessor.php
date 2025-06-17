<?php

require_once 'BaseClass.php';

class ConcreteProcessor extends BaseClass implements Processable 
{
    private array $data;

    public function __construct(string $name) 
    {
        parent::__construct($name);
        $this->data = [];
    }

    public function execute(): void 
    {
        echo "Executing processor {$this->name}\n";
        $this->process();
    }

    public function process(): void 
    {
        echo "Processing data: " . implode(", ", $this->data) . "\n";
    }

    public function getType(): string 
    {
        return "ConcreteProcessor";
    }

    public function addData(string $item): void 
    {
        $this->data[] = $item;
    }
}