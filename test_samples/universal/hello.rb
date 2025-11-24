module Geometry
  class Rectangle
    attr_reader :width, :height
    
    def initialize(width, height)
      @width = width
      @height = height
    end
    
    def area
      @width * @height
    end
  end
end

def greet(name)
  puts "Hello, #{name}!"
end
