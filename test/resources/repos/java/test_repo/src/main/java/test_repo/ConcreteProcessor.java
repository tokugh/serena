package test_repo;

public class ConcreteProcessor extends BaseClass implements Processable {
    private String type;
    
    public ConcreteProcessor(String name, String type) {
        super(name);
        this.type = type;
    }
    
    @Override
    public void process() {
        System.out.println("Processing " + name);
    }
    
    @Override
    public void execute() {
        process();
    }
    
    @Override
    public String getType() {
        return type;
    }
}