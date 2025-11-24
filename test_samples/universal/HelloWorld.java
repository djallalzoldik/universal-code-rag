public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
    
    public int add(int a, int b) {
        return a + b;
    }
}

interface Greeter {
    void greet(String name);
}

enum Color {
    RED, GREEN, BLUE
}
