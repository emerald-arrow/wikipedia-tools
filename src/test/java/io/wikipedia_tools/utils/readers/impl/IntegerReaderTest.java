package io.wikipedia_tools.utils.readers.impl;

import io.wikipedia_tools.configs.Localisation;
import io.wikipedia_tools.enums.Language;
import jdk.jfr.Description;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests of {@link IntegerReader} class.
 */
class IntegerReaderTest {
    private IntegerReader readerMinMax;
    private IntegerReader readerMin;
    private IntegerReader readerMax;

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

        readerMinMax = IntegerReader.builder()
                .message("Enter an integer in [-10, 10].")
                .minValue(-10)
                .maxValue(10)
                .build();

        readerMin = IntegerReader.builder()
                .message("Enter an integer greater than 0.")
                .minValue(1)
                .build();

        readerMax = IntegerReader.builder()
                .message("Enter an integer less than 0.")
                .maxValue(-1)
                .build();
    }

    @ParameterizedTest
    @Description(
            "Successfully reading Integers from user input." +
                    " Min and max values are defined."
    )
    @DisplayName("Integers within interval (min and max)")
    @ValueSource(strings = {"-10", "0", "10"})
    void readValueWithinMinMaxInterval(String input) {
        provideInput(input);

        try {
            assertEquals(Integer.valueOf(input), readerMinMax.read());
        } catch (IOException e) {
            fail(e.getMessage());
        }
    }

    @ParameterizedTest
    @Description(
            "Getting nulls from user input." +
                    " Min and max values are defined."
    )
    @DisplayName("Integers outside interval (min and max)")
    @ValueSource(strings = {"-11", "11"})
    void readValueOutsideMinMaxInterval(String input) {
        provideInput(input);

        try {
            assertNull(readerMinMax.read());
        } catch (IOException e) {
            fail(e.getMessage());
        }
    }

    @Test
    @Description("Getting null from user input. Min value is defined.")
    @DisplayName("Integer outside interval (min defined)")
    void readValueOutsideMinInterval() {
        int smallerThanMin = 0;

        provideInput(String.valueOf(smallerThanMin));

        try {
            assertNull(readerMin.read());
        } catch (IOException e) {
            fail(e.getMessage());
        }
    }

    @Test
    @Description("Getting null from user input. Max value is defined.")
    @DisplayName("Integer outside interval (max defined)")
    void readValueOutsideMaxInterval() {
        int biggerThanMax = 0;

        provideInput(String.valueOf(biggerThanMax));

        try {
            assertNull(readerMax.read());
        } catch (IOException e) {
            fail(e.getMessage());
        }
    }

    @ParameterizedTest
    @Description("Getting exceptions from user input")
    @DisplayName("Exceptions from parsing user input")
    @ValueSource(strings = {"i", "3.14", "-e"})
    void readUnparsableValue(String input) {
        provideInput(input);

        assertThrowsExactly(NumberFormatException.class, () -> readerMinMax.read());
    }
}