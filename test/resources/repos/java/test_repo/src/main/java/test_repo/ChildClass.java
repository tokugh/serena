package test_repo;

public class ChildClass extends BaseClass {
    private int value;
    
    public ChildClass(String name, int value) {
        super(name);
        this.value = value;
    }
    
    @Override
    public void process() {
        System.out.println("Processing " + name + " with value " + value);
    }
    
    public int getValue() {
        return value;
    }
}