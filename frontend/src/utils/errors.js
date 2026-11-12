// A record that does not exist, or one the person may not see, as opposed to a failed request
export const notFound = (error) => error?.exc_type === "DoesNotExistError"
