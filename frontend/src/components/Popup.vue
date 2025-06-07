<template>
  <div v-if="modelValue" class="popup-overlay" @click="closeOnOverlayClick && close()">
    <div class="popup-content" @click.stop>
      <div class="popup-header">
        <h3>{{ title }}</h3>
        <button class="close-button" @click="close">&times;</button>
      </div>
      <div class="popup-body">
        <slot></slot>
      </div>
      <div class="popup-footer">
        <slot name="footer">
          <button class="action-button secondary" @click="close">Cancel</button>
          <button class="action-button primary" @click="$emit('confirm')">Confirm</button>
        </slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Popup',
  props: {
    modelValue: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: 'Popup'
    },
    closeOnOverlayClick: {
      type: Boolean,
      default: true
    }
  },
  emits: ['update:modelValue', 'confirm'],
  methods: {
    close() {
      this.$emit('update:modelValue', false)
    }
  }
}
</script>

<style scoped>
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.popup-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.popup-header h3 {
  margin: 0;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  line-height: 1;
}

.popup-body {
  padding: 20px;
}

.popup-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.action-button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.action-button.primary {
  background-color: #6e8efb;
  color: white;
}

.action-button.primary:hover {
  background-color: #5b74e8;
}

.action-button.secondary {
  background-color: #e0e0e0;
  color: #333;
}

.action-button.secondary:hover {
  background-color: #d0d0d0;
}
</style> 