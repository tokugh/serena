use crate::base::{BaseStruct, Processable, Worker};

// ChildStruct "inherits" from BaseStruct through composition
#[derive(Debug)]
pub struct ChildStruct {
    pub base: BaseStruct,  // Composition - Rust's way of inheritance
    pub value: i32,
}

impl ChildStruct {
    pub fn new(name: String, id: u32, value: i32) -> Self {
        Self {
            base: BaseStruct::new(name, id),
            value,
        }
    }

    pub fn get_value(&self) -> i32 {
        self.value
    }
}

// Implement traits for ChildStruct
impl Processable for ChildStruct {
    fn process(&self) -> Result<(), String> {
        println!("Processing child {} with value {}", self.base.name, self.value);
        Ok(())
    }

    fn get_type(&self) -> String {
        "ChildStruct".to_string()
    }
}

impl Worker for ChildStruct {
    fn execute(&self) {
        println!("Executing child {} with value {}", self.base.name, self.value);
    }

    fn get_worker_id(&self) -> u32 {
        self.base.id
    }
}

// Delegate methods to base
impl std::ops::Deref for ChildStruct {
    type Target = BaseStruct;

    fn deref(&self) -> &Self::Target {
        &self.base
    }
}