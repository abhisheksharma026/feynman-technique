# Feynman Method For Engineering Lessons

Use this pass for every logged entry.

## Steps

1. **Name the misunderstood mechanism**
   Be precise: API envelope shape, React batching, Trino partition pruning, async retry semantics, cache invalidation, schema contract, etc.

2. **Explain it plainly**
   Write 3-5 sentences as if teaching a junior engineer. Define necessary jargon.

3. **Tie it to the real bug**
   Point to the actual file/function/config/query and show how the misunderstanding produced the symptom.

4. **Create a toy example**
   Strip the issue to the smallest example that still preserves the mechanism.

5. **Find the fuzzy part**
   Ask: where did the explanation hand-wave? Common fuzzy areas: ownership, timing, denominator, cache lifetime, retry path, schema variant, or error state.

6. **Repair the gap**
   Re-read source/docs/tests/logs until the fuzzy part becomes concrete. If that is impossible, mark the entry as needing follow-up rather than pretending certainty.

7. **State the transferable rule**
   One sentence that applies outside this bug.

8. **Create a prediction check**
   Ask a question that would predict behavior in a nearby scenario. Example: If the API returns `status=insufficient_data`, which fields are safe to read?

9. **Apply nearby**
   Name one similar route, component, detector, job, query, or config where the same principle should be checked.

## Good Feynman Output

```md
**Feynman explanation:** The endpoint has two success layers: HTTP success and domain success. A 200 response only means the request reached the server; the payload can still say the domain operation failed or has insufficient data.
**Toy example:** `{success:false, data:{status:"insufficient_data", cards:[]}}` is a valid response, so a consumer that assumes cards exist because HTTP was 200 will render the wrong state.
**Where I was fuzzy:** I treated transport success as equivalent to insight readiness.
**Prediction check:** If the endpoint returns 200 with `status:"error"`, should the UI render cards or retry/error state?
**Nearby application:** Check smart-segments and weekly-insights hooks for the same transport-vs-domain assumption.
```
