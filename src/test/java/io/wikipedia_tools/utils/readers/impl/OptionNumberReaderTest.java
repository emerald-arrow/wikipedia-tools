package io.wikipedia_tools.utils.readers.impl;

import io.wikipedia_tools.configs.Localisation;
import io.wikipedia_tools.enums.Language;
import io.wikipedia_tools.utils.readers.InputReader;
import jdk.jfr.Description;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests of {@link OptionNumberReader} class.
 */
class OptionNumberReaderTest {
    private InputReader<Integer> reader;
    private String[] options;

    /**
     * Simulates user input.
     * @param data a {@link String} to be set as user input.
     */
    void provideInput(String data) {
        InputStream stream = new ByteArrayInputStream(
                data.getBytes()
        );

        System.setIn(stream);
    }

    /**
     * Initiates Localisation and sets values of test class fields.
     */
    @BeforeEach
    void init() {
        Localisation.init(Language.ENGLISH);

        this.options = new String[] {
                "Apple", "Banana", "Clementine", "Kiwi", "Mango", "Pear"
        };

        String message = "Pick one fruit from the list below:";

        this.reader = new OptionNumberReader(options, message);
    }

    @ParameterizedTest
    @Description("Successfully read Integers based on given list of options")
    @DisplayName("Successfully read Integers")
    @ValueSource(ints = {1, 3, 5})
    void readOptionNumberSuccess(int number) {
        String expected = this.options[number - 1];

        provideInput(String.valueOf(number));

        try {
            int index = reader.read();
            assertEquals(expected, this.options[index - 1]);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}