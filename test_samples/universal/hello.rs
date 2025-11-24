struct Point {
    x: i32,
    y: i32,
}

impl Point {
    fn new(x: i32, y: i32) -> Point {
        Point { x, y }
    }
    
    fn distance(&self) -> f64 {
        ((self.x.pow(2) + self.y.pow(2)) as f64).sqrt()
    }
}

enum Direction {
    North,
    South,
    East,
    West,
}

fn main() {
    let p = Point::new(10, 20);
    println!("Distance: {}", p.distance());
}
