<template>
  <button
    :class="['base-button', type, { disabled }]"
    :disabled="disabled"
    @click="$emit('click')"
  >
    <slot></slot>
  </button>
</template>

<script>
export default {
  name: "BaseButton",
  props: {
    type: {
      type: String,
      default: "primary", // or "danger", "secondary"
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
};
</script>

<style scoped>
.base-button {
  padding: 0.5rem 1rem;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.base-button:hover {
  transform: scale(1.03);
}

.primary {
  background-color: #6e8efb;
  color: white;
}

.primary:hover {
  background-color: #5b74e8;
}

.danger {
  background-color: #e74c3c;
  color: white;
}

.danger:hover {
  background-color: #c0392b;
}

.secondary {
  background-color: #ddd;
  color: #333;
}

.secondary:hover {
  background-color: #ccc;
}

.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
