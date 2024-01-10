module top_module(
    input clk,
    input load,
    input [255:0] data,
    output reg [255:0] q );
    
    // Parameters 
    parameter N = 16; 
    parameter NX = N + 2;
    
    // Indexing variables
    integer i, row, col; 

    // Create 2D extended grid (for neighbor wrapping) 
    reg [NX-1:0] qx [NX-1:0];

    // Map base 1D-16x16 grid to 2D-18x18
    always @(*) begin
        
        // Top row  { lower right most cell, bottom row, lower left most cell }
        qx[0] = { q[(N*N)-1], q[N*(N-1) +:N], q[N*(N-1)] }; 

        // Middle rows { end of row cell, row of cells, start of row cell}
        for (i=0; i<(N-1); i=i+1)
            qx[i+1] = { q[N*i], q[N*i +:N], q[N*(i+1)-1]};
            
        // Bottom row { upper right most cell, top row, upper left most cell }
        qx[NX-1] = { q[N-1], q[0 +:N], q[0] };
        
    end
    
    // Count alive neighboring cells
    function integer count_alive_neighbors;
        input integer row, col;
        count_alive_neighbors = 
        qx[row-1][col-1] + 	// upper left
        qx[row-1][col]   + 	// above
        qx[row-1][col+1] + 	// upper right
        qx[row][col-1]   + 	// left
        qx[row][col+1]   + 	// right
        qx[row+1][col-1] + 	// lower left
        qx[row+1][col]   + 	// below
        qx[row+1][col+1]; 	// lower right
    endfunction
    
    // Determine if cell should live or die
    function next_cell_state;
        input integer row, col; 
        case (count_alive_neighbors(row, col))
            2: next_cell_state = qx[row][col];
            3: next_cell_state = 1; 
            default: next_cell_state = 0; 
        endcase
    endfunction
               
    // Iterate through and update all cells
    always @(posedge clk) begin
        if (load)
            q <= data;
        else
            for (row = 1; row<(NX-1); row=row+1)
                for (col = 1; col<(NX-1); col=col+1)
                    q[N*(row-1)+(col-1)] <= next_cell_state(row, col);
    end
    
endmodule