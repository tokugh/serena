package test_repo;

interface Readable {
    String read();
}

interface Writable {
    void write(String data);
}

public class MultipleInterfaces implements Readable, Writable, Processable {
    private String data;
    
    public MultipleInterfaces(String data) {
        this.data = data;
    }
    
    @Override
    public String read() {
        return data;
    }
    
    @Override
    public void write(String data) {
        this.data = data;
    }
    
    @Override
    public void execute() {
        System.out.println("Executing with data: " + data);
    }
    
    @Override
    public String getType() {
        return "MultipleInterfaces";
    }
}