<?php

require_once 'BaseClass.php';

class ChildClass extends BaseClass 
{
    private int $value;

    public function __construct(string $name, int $value) 
    {
        parent::__construct($name);
        $this->value = $value;
    }

    public function execute(): void 
    {
        echo "Executing {$this->name} with value {$this->value}\n";
    }

    public function getValue(): int 
    {
        return $this->value;
    }
}