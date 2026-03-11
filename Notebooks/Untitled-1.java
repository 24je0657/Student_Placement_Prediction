
class food{
    
}
class burger extends food{
    
}
class chef {
    food cook(){
        return new food();
    }
}

class fastfoodchef extends chef{
    burger cook(){
        return new burger();
    }
}
