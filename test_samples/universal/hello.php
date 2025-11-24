<?php

trait Loggable {
    public function log($msg) {
        echo "Log: $msg\n";
    }
}

class User {
    use Loggable;
    
    private $name;
    
    public function __construct($name) {
        $this->name = $name;
    }
    
    public function getName() {
        return $this->name;
    }
}

function processUser(User $user) {
    $user->log("Processing " . $user->getName());
}
