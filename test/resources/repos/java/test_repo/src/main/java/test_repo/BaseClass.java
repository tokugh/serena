package test_repo;

public abstract class BaseClass {
    protected String name;
    
    public BaseClass(String name) {
        this.name = name;
    }
    
    public abstract void process();
    
    public String getName() {
        return name;
    }
}