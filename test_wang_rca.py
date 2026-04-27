import wang_rca

def test_add_one_bit():
    wrca = wang_rca.WangAdd()
    num_qubits = 4
    a_vals = [0, 1]
    b_vals = [0, 1]
    c_vals = [0, 1]
    for a in a_vals:
        for b in b_vals:
            for c in c_vals:
                result = wrca.add(a, b, c, num_qubits=num_qubits)
                assert result == a + b, f"Expected {a + b}, got {result}"