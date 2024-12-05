package io.wikipedia_tools.utils.validators.impl;

import io.wikipedia_tools.enums.FileExtension;
import io.wikipedia_tools.utils.validators.Validator;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.regex.Pattern;

/**
 * Class for validating given file path.
 */
public final class FilePathValidator implements Validator {
    private final Path filePath;
    private final FileExtension extension;

    /**
     * The only constructor that takes two arguments.
     * @param filePath a {@link Path} to the file.
     * @param extension a {@link FileExtension} of the file.
     */
    public FilePathValidator(Path filePath, FileExtension extension) {
        this.filePath = filePath;
        this.extension = extension;
    }

    /**
     * Validates file path given in the constructor.
     * @return a boolean - true when the path is valid, false when the path
     * is invalid.
     */
    @Override
    public boolean validate() {
        return extensionValidation() && existenceValidation();
    }

    /**
     * Checks whether the file under given path exists.
     * @return a boolean - true when the file exists, false when the file
     * does not exist.
     */
    private boolean existenceValidation() {
        return Files.exists(filePath);
    }

    /**
     * Checks whether the file under given path has correct extension. The
     * check of the extension is case-insensitive.
     * @return a boolean - true when the extension is correct, false when the
     * extension is incorrect.
     */
    private boolean extensionValidation() {
        Pattern pattern = Pattern.compile(
                ".*\\." + extension.name(),
                Pattern.CASE_INSENSITIVE
        );

        return pattern.matcher(filePath.toString()).find();
    }
}
