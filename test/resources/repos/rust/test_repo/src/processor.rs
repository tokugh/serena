use crate::base::{BaseStruct, Processable, Readable, Writable};

// ConcreteProcessor "inherits" from BaseStruct and implements Processable
#[derive(Debug)]
pub struct ConcreteProcessor {
    pub base: BaseStruct,  // Composition
    data: Vec<String>,
}

impl ConcreteProcessor {
    pub fn new(name: String, id: u32) -> Self {
        Self {
            base: BaseStruct::new(name, id),
            data: Vec::new(),
        }
    }

    pub fn add_data(&mut self, item: String) {
        self.data.push(item);
    }
}

impl Processable for ConcreteProcessor {
    fn process(&self) -> Result<(), String> {
        println!("Processing data in {}: {:?}", self.base.name, self.data);
        Ok(())
    }

    fn get_type(&self) -> String {
        "ConcreteProcessor".to_string()
    }
}

impl std::ops::Deref for ConcreteProcessor {
    type Target = BaseStruct;

    fn deref(&self) -> &Self::Target {
        &self.base
    }
}

// MultipleInterfaces implements multiple traits
#[derive(Debug)]
pub struct MultipleInterfaces {
    data: Vec<u8>,
}

impl MultipleInterfaces {
    pub fn new() -> Self {
        Self { data: Vec::new() }
    }
}

impl Readable for MultipleInterfaces {
    fn read(&self) -> Result<Vec<u8>, String> {
        Ok(self.data.clone())
    }
}

impl Writable for MultipleInterfaces {
    fn write(&mut self, data: &[u8]) -> Result<(), String> {
        self.data = data.to_vec();
        Ok(())
    }
}

impl Processable for MultipleInterfaces {
    fn process(&self) -> Result<(), String> {
        println!("Processing data: {:?}", String::from_utf8_lossy(&self.data));
        Ok(())
    }

    fn get_type(&self) -> String {
        "MultipleInterfaces".to_string()
    }
}