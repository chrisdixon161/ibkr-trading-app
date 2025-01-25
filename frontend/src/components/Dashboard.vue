<template>
	<div class="dashboard">
		<h1 class="text-2xl font-bold mb-4">IBKR Dashboard</h1>

		<!-- Section to display errors -->
		<p v-if="error" class="text-red-500">Error: {{ error }}</p>

		<!-- Section to retrieve IBKR account data -->
		<div class="card mb-6">
			<h2 class="text-xl font-semibold mb-2">Retrieve Account Data</h2>
			<button
				@click="fetchAccountData"
				class="btn bg-blue-500 text-white hover:bg-blue-600"
			>
				Get Account Data
			</button>
			<div v-if="accountData" class="mt-4">
				<h3 class="font-semibold">Account Summary:</h3>
				<div v-for="(item, index) in accountData" :key="index">
					<p v-if="item.tag === 'TotalCashBalance' && item.currency === 'BASE'">
						<strong>Total Cash Balance: </strong>{{ item.value }}
					</p>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";

const accountData = ref(null);
const tradeData = ref({
	symbol: "",
	expiry: "",
	strike: null,
	right: "C", // Default to Call
	quantity: 1,
	action: "BUY", // Default to Buy
	order_type: "MKT", // Default to Market Order
	limit_price: null, // Only used for Limit Orders
});
const tradeResponse = ref(null);
const error = ref(null);

const fetchAccountData = async () => {
	try {
		const response = await axios.get(
			"http://127.0.0.1:8000/api/ibkr/account-data"
		);
		accountData.value = response.data.account_data;
		error.value = null;
	} catch (err) {
		console.error("Error fetching account data:", err);
		error.value =
			err.response?.data?.detail || "Failed to retrieve account data.";
	}
};

const placeTrade = async () => {
	try {
		const response = await axios.post(
			"http://127.0.0.1:8000/api/ibkr/place-option-trade",
			tradeData.value
		);
		tradeResponse.value = response.data;
		error.value = null;
	} catch (err) {
		console.error("Error placing trade:", err);
		error.value = err.response?.data?.detail || "Failed to place trade.";
	}
};
</script>

<style scoped>
.card {
	padding: 1rem;
	margin-bottom: 1rem;
	border: 1px solid #e5e7eb;
	border-radius: 0.5rem;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.input {
	width: 100%;
	padding: 0.5rem;
	margin-top: 0.25rem;
	border: 1px solid #e5e7eb;
	border-radius: 0.25rem;
}
.btn {
	padding: 0.5rem 1rem;
	font-weight: 500;
	border-radius: 0.25rem;
	cursor: pointer;
}
</style>
