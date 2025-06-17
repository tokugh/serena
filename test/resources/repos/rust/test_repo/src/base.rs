// Base trait definitions for inheritance testing

pub trait Processable {
    fn process(&self) -> Result<(), String>;
    fn get_type(&self) -> String;
}

pub trait Readable {
    fn read(&self) -> Result<Vec<u8>, String>;
}

pub trait Writable {
    fn write(&mut self, data: &[u8]) -> Result<(), String>;
}

// Base struct that can be "inherited" through composition
#[derive(Debug, Clone)]
pub struct BaseStruct {
    pub name: String,
    pub id: u32,
}

impl BaseStruct {
    pub fn new(name: String, id: u32) -> Self {
        Self { name, id }
    }

    pub fn execute(&self) {
        println!("Executing base with name: {}, ID: {}", self.name, self.id);
    }

    pub fn get_name(&self) -> &str {
        &self.name
    }
}

// Trait that extends other traits
pub trait Worker: Processable {
    fn execute(&self);
    fn get_worker_id(&self) -> u32;
}