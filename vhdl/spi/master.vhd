library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity spi_master is
    generic (
        CLK_DIV : integer := 4;  -- System clock divider to generate SCLK
        DATA_WIDTH : integer := 8 -- Data width in bits
    );
    port (
        -- Control signals
        clk         : in  std_logic;
        rst         : in  std_logic;
        enable      : in  std_logic;
        cpol       : in  std_logic;  -- Clock polarity
        cpha       : in  std_logic;  -- Clock phase

        -- Data signals
        data_in     : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        data_out    : out std_logic_vector(DATA_WIDTH-1 downto 0);
        data_valid  : out std_logic;
        busy        : out std_logic;

        -- SPI interface
        sclk        : out std_logic;
        mosi        : out std_logic;
        miso        : in  std_logic;
        ss_n        : out std_logic
    );
end entity spi_master;

architecture rtl of spi_master is
    type state_type is (IDLE, TRANSFER, COMPLETE);
    signal state : state_type;

    signal bit_counter : integer range 0 to DATA_WIDTH-1;
    signal clock_counter : integer range 0 to CLK_DIV-1;
    signal shift_reg : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal sclk_internal : std_logic;
    signal transfer_active : std_logic;

begin
    process(clk, rst)
    begin
        if rst = '1' then
            state <= IDLE;
            bit_counter <= 0;
            clock_counter <= 0;
            shift_reg <= (others => '0');
            sclk_internal <= cpol;
            transfer_active <= '0';
            ss_n <= '1';
            data_valid <= '0';
            busy <= '0';

        elsif rising_edge(clk) then
            case state is
                when IDLE =>
                    sclk_internal <= cpol;
                    ss_n <= '1';
                    data_valid <= '0';

                    if enable = '1' then
                        state <= TRANSFER;
                        shift_reg <= data_in;
                        bit_counter <= DATA_WIDTH-1;
                        transfer_active <= '1';
                        ss_n <= '0';
                        busy <= '1';
                    end if;

                when TRANSFER =>
                    if clock_counter = CLK_DIV-1 then
                        clock_counter <= 0;
                        sclk_internal <= not sclk_internal;

                        -- Sample or shift based on CPHA
                        if (cpha = '0' and sclk_internal = '0') or
                           (cpha = '1' and sclk_internal = '1') then
                            -- Shift out next bit
                            mosi <= shift_reg(DATA_WIDTH-1);
                            shift_reg <= shift_reg(DATA_WIDTH-2 downto 0) & '0';
                        else
                            -- Sample input bit
                            shift_reg(0) <= miso;
                        end if;

                        -- Update bit counter
                        if ((cpha = '0' and sclk_internal = '1') or
                            (cpha = '1' and sclk_internal = '0')) and
                            bit_counter = 0 then
                            state <= COMPLETE;
                        elsif (cpha = '0' and sclk_internal = '1') or
                              (cpha = '1' and sclk_internal = '0') then
                            bit_counter <= bit_counter - 1;
                        end if;
                    else
                        clock_counter <= clock_counter + 1;
                    end if;

                when COMPLETE =>
                    ss_n <= '1';
                    transfer_active <= '0';
                    data_valid <= '1';
                    data_out <= shift_reg;
                    busy <= '0';
                    state <= IDLE;
            end case;
        end if;
    end process;

    -- Output assignments
    sclk <= sclk_internal when transfer_active = '1' else cpol;

end architecture rtl;
