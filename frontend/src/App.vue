<script setup>
import { onMounted, ref } from "vue";
import Account from "./components/Account.vue";
import Login from "./components/Login.vue";
import { supabase } from "./supabase";

const session = ref();

onMounted(() => {
	supabase.auth.getSession().then(({ data }) => {
		session.value = data.session;
	});

	supabase.auth.onAuthStateChange((_, _session) => {
		session.value = _session;
	});
});
</script>

<template>
	<div>
		<header>
			<div class="wrapper">
				<Account v-if="session" :session="session" />
				<Login v-else />
			</div>
		</header>

		<RouterView />
	</div>
</template>

<style scoped></style>
