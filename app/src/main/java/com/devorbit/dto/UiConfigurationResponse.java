package com.devorbit.dto;

import java.util.List;

/**
 * Runtime configuration consumed by the bundled UI. Keeping this contract on
 * the server prevents a static browser build from inventing deployment values.
 */
public record UiConfigurationResponse(
        String title,
        String subtitle,
        List<StatusOption> statuses,
        EndpointConfiguration endpoints,
        FormConfiguration form
) {
    public record StatusOption(String value, String label) {
    }

    public record EndpointConfiguration(String health, String issues) {
    }

    public record FormConfiguration(int titleMinLength, int titleMaxLength,
                                    int descriptionMinLength, int descriptionMaxLength) {
    }
}
