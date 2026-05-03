from turing_system.tokenSystem import (
    
    REST_KEYWORDS,
    TokenType,

)


class Tape:

    def __init__(self, first_chain: "Chain") -> None:
        
        self.first_chain = first_chain
        self.on_chain = first_chain

        self.index: int = 0

        return None

    def get_chain(self) -> "Chain":

        return self.on_chain

    def go_left(self) -> "Chain":

        chain = self.on_chain.get_left()
        
        if chain is None:
            new_chain = Chain(REST_KEYWORDS[TokenType.NONE])
            self.on_chain.link_on_left(new_chain)
            new_chain.link_on_right(self.on_chain)
            chain = new_chain

        self.on_chain = chain
        self.index -= 1

        return self.on_chain 

    def go_right(self) -> "Chain":

        chain = self.on_chain.get_right()
        
        if chain is None:
            new_chain = Chain(REST_KEYWORDS[TokenType.NONE])
            self.on_chain.link_on_right(new_chain)
            new_chain.link_on_left(self.on_chain)
            chain = new_chain

        self.on_chain = chain
        self.index += 1

        return self.on_chain 

    def get_index(self) -> int:

        return self.index

    def reset_indexisation(self, index: int = 0) -> None:

        self.index = 0
        self.on_chain = self.first_chain
        
        if index > 0:
            while self.index < index:
                self.go_right()
        
        elif index < 0:
            while self.index > index:
                self.go_left()
        
        return None

    def __str__(self) -> str:
        
        result = f"Tape({self.first_chain}"

        index_chain = self.first_chain.link_right

        while index_chain is not None:
            result += f"<->{index_chain}"
            index_chain = index_chain.link_right

        result += f", idx: {self.on_chain}, first_chain: {self.first_chain})"

        return result

class Chain:

    def __init__(self, value: str, 
                 link_left: "Chain | None" = None, 
                 link_right: "Chain | None" = None) -> None:
        
        self.value = value

        self.link_left  = link_left
        self.link_right = link_right

        return None

    def get_value(self) -> str:

        return self.value
    
    def set_value(self, value: str) -> None:

        self.value = value

    def get_left(self) -> "Chain | None":

        return self.link_left

    def get_right(self) -> "Chain | None":
        
        return self.link_right

    def link_on_left(self, link_left: "Chain | None") -> None:

        self.link_left = link_left
        return None

    def link_on_right(self, link_right: "Chain | None") -> None:

        self.link_right = link_right
        return None
    
    def __str__(self) -> str:
        return f"Chain(\"{self.value}\")"