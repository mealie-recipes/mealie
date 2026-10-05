<?php

namespace App\Http\Controllers;

use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

final class ParserController extends Controller
{
    public function ingredient(Request $request): JsonResponse
    {
        $text = (string) $request->input('ingredient', '');

        return response()->json($this->parse($text));
    }

    public function ingredients(Request $request): JsonResponse
    {
        $lines = $request->input('ingredients', []);
        if (! is_array($lines)) {
            $lines = [];
        }

        return response()->json(array_map(fn ($line) => $this->parse((string) $line), $lines));
    }

    /**
     * @return array<string, mixed>
     */
    private function parse(string $text): array
    {
        $quantity = 0.0;
        $note = trim($text);
        if (preg_match('/^\s*(\d+(?:[./]\d+)?)\s+(.*)$/', $text, $matches) === 1) {
            $raw = $matches[1];
            if (str_contains($raw, '/')) {
                [$num, $den] = explode('/', $raw, 2);
                $quantity = ((float) $den) == 0.0 ? 0.0 : ((float) $num / (float) $den);
            } else {
                $quantity = (float) $raw;
            }
            $note = trim($matches[2]);
        }

        return [
            'input' => $text,
            'confidence' => [
                'average' => 0.4,
                'comment' => 0.4,
                'name' => null,
                'unit' => null,
                'quantity' => $quantity > 0 ? 0.8 : null,
                'food' => null,
            ],
            'ingredient' => [
                'quantity' => $quantity,
                'unit' => null,
                'food' => null,
                'note' => $note,
                'display' => trim($text),
                'title' => null,
                'originalText' => $text,
                'referenceId' => null,
                'substitutions' => [],
            ],
        ];
    }
}
