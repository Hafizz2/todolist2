<?php
declare(strict_types=1);

function json_response(array $data, int $status = 200): never
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
    exit;
}

function json_error(string $error, int $status): never
{
    json_response(['error' => $error], $status);
}

function require_method(string $method): void
{
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== $method) {
        header("Allow: $method");
        json_error('method_not_allowed', 405);
    }
}

function read_json_body(): array
{
    $body = json_decode((string) file_get_contents('php://input'), true);
    if (!is_array($body)) {
        json_error('invalid_json', 400);
    }
    return $body;
}
