package io.wikipedia_tools.utils.validators.impl;

import io.wikipedia_tools.enums.FileExtension;
import io.wikipedia_tools.utils.validators.Validator;
import jdk.jfr.Description;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.*;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.*;

class FilePathValidatorTest {

    @TempDir
    private static Path tempDir;

    @ParameterizedTest
    @DisplayName("File path validation - success")
    @Description(
            "Successful validation of file paths with different cases of" +
                    "extensions"
    )
    @MethodSource("provideParametersSuccess")
    void validateSuccess(
            String fileName, String extension, FileExtension fileExtension
    ) {
        Path path = null;

        try {
            path = createTempFile(fileName, extension);
        } catch (IOException e) {
            fail(e.getMessage());
        }

        Validator validator = new FilePathValidator(path, fileExtension);

        assertTrue(validator.validate());
    }

    @Test
    @DisplayName("File path validation - fail (extension)")
    @Description("Failed validation of file path due to wrong extension")
    void validateFailExtension() {
        final String filePath = "03_Classification_Qualifying";
        final String actualExtension = ".json";

        Path path = null;

        try {
            path = createTempFile(filePath, actualExtension);
        } catch (IOException e) {
            fail(e.getMessage());
        }

        FileExtension expectedExtension = FileExtension.CSV;

        Validator validator = new FilePathValidator(path, expectedExtension);

        assertFalse(validator.validate());
    }

    @Test
    @DisplayName("File path validation - fail (nonexistent)")
    @Description(
            "Failed validation of file path due to the file not existing"
    )
    void validateFailNotExists() {
        final String fileName = "03_Classification_Qualifying";
        final String extension = ".csv";
        FileExtension fileExtension = FileExtension.CSV;

        Path path = null;

        try {
            path = createTempFile(fileName, extension);
        } catch (IOException e) {
            fail(e.getMessage());
        }

        try {
            Files.delete(path);
        } catch (IOException e) {
            fail(e.getMessage());
        }

        Validator validator = new FilePathValidator(path, fileExtension);

        assertFalse(validator.validate());
    }

    /**
     * Provides parameters for validateSuccess testing method.
     * @return a {@link Stream} of {@link Arguments} for validateSuccess
     * method.
     */
    private static Stream<Arguments> provideParametersSuccess() {
        return Stream.of(
                Arguments.of(
                        "03_Classification_Free Practice 1",
                        ".CSV",
                        FileExtension.CSV
                ),
                Arguments.of(
                        "03_Classification_Qualifying",
                        ".Csv",
                        FileExtension.CSV
                ),
                Arguments.of(
                        "03_Classification_Race_Hour_6",
                        ".csv",
                        FileExtension.CSV
                )
        );
    }

    /**
     * Creates a temporary file in the temporary directory.
     * @param fileName a {@link String} with file name.
     * @param extension a String with file's extension.
     * @return a {@link Path} to the created temporary file.
     * @throws IOException when an I/O operation fails or is interrupted.
     */
    private Path createTempFile(String fileName, String extension)
            throws IOException {
        return Files.createTempFile(
                tempDir,
                fileName,
                extension
        );
    }
}